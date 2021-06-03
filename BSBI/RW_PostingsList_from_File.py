from io import FileIO
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

import bytebuffer as bytebuffer

from PostingList import PostingList


class ReadWrite:

    def read_posting(self, io: FileIO) -> PostingList:
        Buf: bytebuffer.ByteBuffer
        termID: int
        docFreq: int
        docID: int
        each_postlist: list[int] = []
        buf = bytebuffer.ByteBuffer.allocate(4)
        try:
            if io.read(buf) <= 0:
                return None
        except Exception as e:
            logger.error(str(e), exc_info=True)
        buf.flip()
        termID = buf.get_UBInt32()

        buf = bytebuffer.ByteBuffer.allocate(4)
        try:
            io.read(buf)
        except Exception as e:
            logger.error(str(e), exc_info=True)
        buf.flip()
        docFreq = buf.get_UBInt32()

        for i in range(0, docFreq):
            buf = bytebuffer.ByteBuffer.allocate(4)
            try:
                io.read(buf)
            except Exception as e:
                logger.error(str(e), exc_info=True)
            buf.flip()
            docID = buf.get_UBInt32()
            each_postlist.append(docID)

        postlist: PostingList = PostingList(termID, each_postlist)
        return postlist


    def write_posting(self, io: FileIO, postinglist: PostingList):
        buf: bytebuffer.ByteBuffer
        term_id: int
        doc_freq: int

        buf = bytebuffer.ByteBuffer.allocate((len(postinglist.postings)+2)*4)
        term_id = postinglist.term_id
        doc_freq = len(postinglist.postings)

        buf.put_UBInt32(term_id)
        buf.put_UBInt32(doc_freq)

        for i in range(0, len(postinglist.postings)):
            buf.put_UBInt32(postinglist.postings[i])

        buf.flip()

        while buf.has_remaining():
            try:
                io.write(buf)
            except Exception as e:
                logger.error(str(e), exc_info=True)


